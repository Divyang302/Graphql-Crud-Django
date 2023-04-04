import graphene
from graphene_django import DjangoObjectType
from .models import *
from graphql import GraphQLError
from graphene import ObjectType
from .helper import *
from graphene.types.generic import GenericScalar


class TemplateDetailsType(DjangoObjectType):
    class Meta:
        model = TemplateDetails
        fileds = '__all__'


class FieldDetailsType(DjangoObjectType):
    class Meta:
        model = FieldDetails
        fileds = '__all__'


class GetTemplateDetailsType(graphene.ObjectType):
    TemplateId = graphene.String()
    TemplateName = graphene.String()
    TemplateTitle = graphene.String()
    TemplateField = graphene.List(FieldDetailsType, required=False)



class GetAllRecordType(graphene.ObjectType):
    record = graphene.List(GenericScalar)


class PickListInput(graphene.InputObjectType):
    name = graphene.String(required=False)


class TemplateGroupInput(graphene.InputObjectType):
    id = graphene.ID(required=False)
    templatName = graphene.String(required=False)


class FieldGroupInput(graphene.InputObjectType):
    id = graphene.ID(required=False)
    label = graphene.String(required=False)
    type = graphene.String(required=False)
    maxValue = graphene.String(required=False)
    decimalPoint = graphene.String(required=False)
    pickList = graphene.List(graphene.String)
    title = graphene.String(required=False)

class CreateTemplateDetailsMutation(graphene.Mutation):
    class Arguments:
        templatName = graphene.String(required=True)
        templateField = graphene.List(FieldGroupInput, required=False)
    msg = GenericScalar()
    template = graphene.String()

    @classmethod
    def mutate(cls, root, info, templatName, templateField):
        try:
            x = {"template_fields": templateField, "template_name": templatName}
            respose = create_template_and_field(**x)
            return CreateTemplateDetailsMutation(msg=respose)
        except Exception as ex:
            return GraphQLError(str(ex))


class updateTemplateDetailsMutation(graphene.Mutation):
    class Arguments:
        templateID = graphene.ID(required=False)
        templatName = graphene.List(TemplateGroupInput, required=False)
        templateField = graphene.List(FieldGroupInput, required=False)
    msg = GenericScalar()

    @classmethod
    def mutate(cls, root, info, templatName=None, templateField=None, templateID=None):
        try:
            x = {"template_fields": templateField,
                 "template_name": templatName, "template_id": templateID}
            respose = update_tempalte_and_field(**x)
        except Exception as ex:
            return GraphQLError(str(ex))
        return updateTemplateDetailsMutation(msg=respose)


class DeleteTemplateDetailsMutation(graphene.Mutation):
    class Arguments:
        templateId = graphene.ID()
        fieldId = graphene.ID()
    msg = GenericScalar()

    @classmethod
    def mutate(cls, root, info, templateId=None, fieldId=None):
        try:
            x = {"templateid": templateId, "fieldid": fieldId}
            respose = delete_tempalte_and_field(**x)
        except Exception as ex:
            return GraphQLError(str(ex))
        return updateTemplateDetailsMutation(msg=respose)


class IsertDataFromField(graphene.Mutation):
    class Arguments:
        TemplateName = graphene.String()
        TemplateRecord = GenericScalar()
    msg = GenericScalar()

    @classmethod
    def mutate(cls, root, info, **insert_data):
        try:
            x = {"TemplateName": insert_data['TemplateName'], "TemplateRecord": insert_data.get('TemplateRecord', {})}
            respose = insert_data_from_fields(**x)
            return IsertDataFromField(msg=respose)
        except Exception as ex:
            return GraphQLError(str(ex))


class UpdateDataFromField(graphene.Mutation):
    class Arguments:
        TemplateName = graphene.String()
        TemplateRecord = GenericScalar()
    msg = GenericScalar()

    @classmethod
    def mutate(cls, root, info, **update_data):
        try:
            x = {"TemplateName": update_data['TemplateName'], "TemplateRecord": update_data.get('TemplateRecord', {})}
            respose = update_data_from_fields(**x)
            return UpdateDataFromField(msg=respose)
        except Exception as ex:
            return GraphQLError(str(ex))


class DeleteDataFromField(graphene.Mutation):
    class Arguments:
        TemplateName = graphene.String()
        RecordId = graphene.ID()
    msg = GenericScalar()

    @classmethod
    def mutate(cls, root, info, **delete_data):
        try:
            x = {
                "TemplateName": delete_data['TemplateName'], "RecordId": delete_data['RecordId']}
            respose = delete_data_from_fields(**x)
            return DeleteDataFromField(msg=respose)
        except Exception as ex:
            return GraphQLError(str(ex))


class Mutation(graphene.ObjectType):
    create_template = CreateTemplateDetailsMutation.Field()
    update_template = updateTemplateDetailsMutation.Field()
    delete_template = DeleteTemplateDetailsMutation.Field()
    insert_data_from_field = IsertDataFromField.Field()
    update_data_from_field = UpdateDataFromField.Field()
    delete_data_from_field = DeleteDataFromField.Field()


class Query(graphene.ObjectType):
    get_all_template_data = graphene.List(GetTemplateDetailsType)
    get_template_by_id = graphene.Field(
        GetTemplateDetailsType, id=graphene.ID())
    get_record_by_template_name = graphene.Field(
        GetAllRecordType, templateName=graphene.String())

    def resolve_get_all_template_data(root, info):
        templateOutput = []
        templateDataList = TemplateDetails.objects.all()
        for i in templateDataList:
            fieldData = FieldDetails.objects.filter(templateid__id=i.id)
            tempObject = {
                "TemplateId": i.id,
                "TemplateName": i.template_name,
                "TemplateTitle":i.title,
                "TemplateField": fieldData
            }
            templateOutput.append(tempObject)
        return templateOutput

    def resolve_get_template_by_id(root, info, id):
        templateDataList = TemplateDetails.objects.get(id=id)
        fieldData = FieldDetails.objects.filter(
            templateid__id=templateDataList.id)
        tempObject = {
            "TemplateId": templateDataList.id,
            "TemplateName": templateDataList.template_name,
            "TemplateTitle":templateDataList.title,
            "TemplateField": fieldData,
        }
        return tempObject

    def resolve_get_record_by_template_name(root, info, templateName):
        allrecord = {
            "record": get_record_data(templateName)
        }
        return allrecord


schema = graphene.Schema(query=Query, mutation=Mutation)
