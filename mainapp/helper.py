import json
from .models import *
import psycopg2
import datetime
from psycopg2 import Error
import decimal
from graphql import GraphQLError
from decouple import config

Connection = psycopg2.connect(user="postgres",
                              password=config('PASSWORD'),
                              host=config('HOST'),
                              port=config('PORT'),
                              database=config('DATABASENAME'))
cursor = Connection.cursor()


def create_template_and_field(**template_data):

    try:
        try:
            table_name = template_data['template_name'].replace(" ", "_")
            table_name = table_name.lower()
            obj = TemplateDetails(
                template_name=table_name,
                title=template_data['template_name']
            )
            obj.save()

            create_table_query = f'''CREATE TABLE {table_name}(ID SERIAL PRIMARY KEY); '''
            cursor.execute(create_table_query)
            Connection.commit()
        except:
            Connection.commit()
            e = {"error": 'Template already exist...'}
            return e

        for i in template_data['template_fields']:
            print(i)
            if i["type"] == "DECIMAL(15,)":
                type = "DECIMAL(15,{})".format(int(i['decimalPoint']))
            elif i["type"] == "CHAR()":
                type = f"CHAR({i['maxValue']})"
            else:
                type = i["type"]

            label = i['label'].replace(" ", "_")
            label = label.lower()
            field = FieldDetails(
                label=label if label != "" else None,
                type=type if type != "" else None,
                maxValue=int(i["maxValue"]) if i["maxValue"] != "" else None,
                pickList=i["pickList"] if i["pickList"] != "" else None,
                decimalPoint=i["decimalPoint"] if i["decimalPoint"] != "" else "",
                title=i['label'],
                templateid=obj,
            )
            field.save()
            try:
                label = i['label'].replace(" ", "_")
                if type == "M_Json":
                    type = "Json"
                # if i["decimalPoint"] != "":
                #     type = "DECIMAL(15,{})".format(int(i['decimalPoint']))

                create_table_field = f"ALTER TABLE {table_name} ADD COLUMN {label}  {type} ;"
                cursor.execute(create_table_field)

            except Exception as ex:
                if (Connection):
                    Connection.commit()
                    e = {"error": str(ex)}
                    return e
        Connection.commit()
    except Exception as ex:
        Connection.commit()
        e = {"error": str(ex)}
        return e
    m = {"message": 'Template and fields are created successfully.'}
    return m


def update_tempalte_and_field(**template_data):

    try:
        if (template_data['template_name'] != None and template_data['template_name'] != '') or template_data['template_id'] != None:
            try:
                if template_data['template_fields'] != "" and template_data['template_fields'] != None:
                    fieldid = template_data['template_fields'][0]['id']
                    templateid = template_data['template_id']
                    if fieldid:
                        fielddata = FieldDetails.objects.filter(
                            id=int(fieldid))
                        if fielddata[0].templateid.id == int(templateid):
                            if len(fielddata) == 1:
                                i = dict(template_data['template_fields'][0])

                                table_name = fielddata[0].templateid.template_name
                                table_name = table_name.lower()
                                old_column_name = fielddata[0].label

                                if i["type"] == "DECIMAL(15,)":
                                    type = "DECIMAL(15,{})".format(
                                        int(i['decimalPoint']))
                                elif i["type"] == "CHAR()":
                                    type = f"CHAR({i['maxValue']})"
                                else:
                                    type = i["type"]

                                label = i['label'].replace(" ", "_")

                                fielddata = fielddata[0]
                                fielddata.label = label if label != "" else None
                                fielddata.type = type if type != "" else None
                                fielddata.maxValue = int(
                                    i["maxValue"]) if i["maxValue"] != "" else None
                                fielddata.pickList = i["pickList"] if i["pickList"] != "" else None
                                fielddata.decimalPoint = i["decimalPoint"] if i["decimalPoint"] != "" else ""
                                fielddata.title = i['label']
                                fielddata.save()

                                field_update = f"ALTER TABLE {table_name} RENAME COLUMN {old_column_name} TO {label};"
                                cursor.execute(field_update)
                                Connection.commit()
                                m = {"message": 'field name is updateed.'}
                                return m
                            else:
                                e = {"error": 'field is not found.'}
                                return e
                        else:
                            e = {"error": f'this field is not the template of {id}'}
                            return e
                else:
                    id = template_data['template_name'][0]['id']
                    if id:
                        templatedata = TemplateDetails.objects.get(id=id)
                        new_table_name = template_data['template_name'][0]['templatName'].replace(
                            " ", "_")
                        if templatedata:
                            old_name = templatedata.template_name
                            templatedata.template_name = new_table_name
                            templatedata.title = template_data['template_name'][0]['templatName']
                            templatedata.save()
                            table_rename = f"ALTER TABLE {old_name} RENAME TO {new_table_name};"
                            cursor.execute(table_rename)
                            Connection.commit()
                            m = {"message": 'Template name is updated.'}
                            return m
                        else:
                            e = {"error": 'Template is not found.'}
                            return e
                    else:
                        e = {"error": 'Tempalename is missing'}
                        return e
            except Exception as ex:
                Connection.commit()
                e = {"error": str(ex)}
                return e
        else:
            e = {"error": 'Template name is missing'}
            return e
    except Exception as ex:
        Connection.commit()
        e = {"error": str(ex)}
        return e


def delete_tempalte_and_field(**template_data):

    try:
        if (template_data['templateid'] != None and template_data['templateid'] != '') or template_data['fieldid'] != None:
            if template_data['fieldid']:
                fieldid = template_data['fieldid']
                if fieldid:
                    fielddata = FieldDetails.objects.get(id=fieldid)
                    table_name = fielddata.templateid.template_name
                    field_name = fielddata.label
                    if fielddata:
                        fielddata.delete()
                        alter_column = f"ALTER TABLE {table_name} DROP COLUMN {field_name};"
                        cursor.execute(alter_column)
                        Connection.commit()
                        m = {"message": 'field name is deleted.'}
                        return m
                    else:
                        e = {"error": 'field is not found.'}
                        return e

            else:
                templateid = template_data['templateid']
                if templateid:
                    templatedata = TemplateDetails.objects.get(id=templateid)
                    table_name = templatedata.template_name
                    if templatedata:
                        releted_template_field = FieldDetails.objects.filter(
                            templateid__id=templateid)
                        for i in releted_template_field:
                            i.delete()
                        templatedata.delete()

                        drop_table = f"DROP TABLE {table_name};"
                        cursor.execute(drop_table)
                        Connection.commit()
                        m = {"message": 'Template name is delete.'}
                        return m
                    else:
                        e = {"error": 'Template is not found.'}
                        return e
                else:
                    e = {"error": 'Tempalename is missing'}
                    return e
        else:
            e = {"error": 'Template name is missing'}
            return e
    except Exception as ex:
        Connection.commit()
        e = {"error": str(ex)}
        return e


def insert_data_from_fields(**data):

    TemplateName = data['TemplateName']
    TemplateRecord = data['TemplateRecord']
    try:
        id = None
        for k, v in TemplateRecord.items():
            try:
                sql = 'INSERT INTO {table_name}({key}) VALUES ({value}) RETURNING id;'
                sql_where = 'UPDATE {table_name} SET {key} = {value} WHERE id = {id} ;'
                if id == None:
                    if type(v) == str:
                        v = "'"+v+"'"
                        sql = sql.format(
                            table_name=TemplateName, key=k, value=v)
                    elif type(v) == list:
                        v = json.dump(v)
                        v = "'"+v+"'"
                        sql = sql.format(
                            table_name=TemplateName, key=k, value=v)
                    else:
                        sql = sql.format(
                            table_name=TemplateName, key=k, value=v)
                    cursor.execute(sql)
                    id = cursor.fetchone()[0]
                    Connection.commit()
                else:
                    type(v)
                    if type(v) == str and v != "" and v != None:
                        v = "'"+v+"'"
                        sql_where = sql_where.format(
                            table_name=TemplateName, key=k, value=v, id=id)
                    elif type(v) == list:
                        v = json.dumps(v)
                        v = "'"+v+"'"
                        sql_where = sql_where.format(
                            table_name=TemplateName, key=k, value=v, id=id)
                    elif v == '' or v == None or v == "":
                        continue
                    else:
                        v = str(v)
                        sql_where = sql_where.format(
                            table_name=TemplateName, key=k, value=v, id=id)
                    cursor.execute(sql_where)
                    Connection.commit()
            except (Exception, Error) as error:
                Connection.commit()
                e = {
                    "error": "Error while inserting data into to PostgreSQL" + str(error)}
                return e
        m = {"message": "data successfully enterd"}
        return m
    except Exception as ex:
        Connection.commit()
        e = {"error": str(ex)}
        return e


def update_data_from_fields(**data):

    TemplateName = data['TemplateName']
    TemplateRecord = data['TemplateRecord']

    try:
        id = None
        for k, v in TemplateRecord.items():
            try:
                # sql = 'INSERT INTO {table_name}({key}) VALUES ({value}) RETURNING id;'
                sql_where = 'UPDATE {table_name} SET {key} = {value} WHERE id = {id} ;'

                if str(k) != "id":
                    type(v)
                    if type(v) == str and v != "" and v != None:
                        v = "'"+v+"'"
                        sql_where = sql_where.format(
                            table_name=TemplateName, key=k, value=v, id=id)
                    elif type(v) == list:
                        v = json.dumps(v)
                        v = "'"+v+"'"
                        sql_where = sql_where.format(
                            table_name=TemplateName, key=k, value=v, id=id)
                    elif v == '' or v == None or v == "":
                        continue
                    else:
                        v = str(v)
                        sql_where = sql_where.format(
                            table_name=TemplateName, key=k, value=v, id=id)
                    cursor.execute(sql_where)
                    Connection.commit()
                elif str(k) == "id":
                    id = v

            except (Exception, Error) as error:
                Connection.commit()
                e = {
                    "error": "Error while Updateing data into to PostgreSQL" + str(error)}
                return e
        m = {"message": "data  update successfully enterd"}
        return m
    except Exception as ex:
        Connection.commit()
        e = {"error": str(ex)}
        return e


def delete_data_from_fields(**data):

    try:
        TemplateName = data['TemplateName']
        RecordId = data['RecordId']
        query = f"Delete from {TemplateName} where id = {RecordId}"
        cursor.execute(query)
        Connection.commit()
        print(RecordId)
        print(TemplateName)
        m = {"message":  'Filed deleted success fully.'}
        return m
    except (Exception, Error) as error:
        Connection.commit()
        e = {
            "error": f"Error while inserting data into to PostgreSQL, {str(error)}"}
        return e


def get_record_data(templateName):

    try:
        query = f"SELECT * from {templateName}"
        cursor.execute(query)
        Connection.commit()
        r = [dict((cursor.description[i][0], value.strftime("%m/%d/%Y") if type(value) == datetime.date else float(value)
                  if type(value) == decimal.Decimal else value) for i, value in enumerate(row)) for row in cursor.fetchall()]
        # print(r)
        return r

    except (Exception, Error) as error:
        Connection.commit()
        e = {
            "error": "Error while getting data into to PostgreSQL" + str(error)}
        return e
